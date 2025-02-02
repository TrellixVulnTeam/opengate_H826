/* --------------------------------------------------
   Copyright (C): OpenGATE Collaboration
   This software is distributed under the terms
   of the GNU Lesser General  Public Licence (LGPL)
   See LICENSE.md for further details
   ------------------------------------ -------------- */

#include "GateARFTrainingDatasetActor.h"
#include "G4RandomTools.hh"
#include "G4RunManager.hh"
#include "GateActorManager.h"
#include "GateHelpersDict.h"
#include "GateHitsCollectionManager.h"
#include "GateTHitAttribute.h"

GateARFTrainingDatasetActor::GateARFTrainingDatasetActor(py::dict &user_info)
    : GateHitsCollectionActor(user_info) {
  // action
  fActions.insert("EndOfEventAction");
  // options
  fInputActorName = DictGetStr(user_info, "energy_windows_actor");
  fEnergyWindowsActor = dynamic_cast<GateHitsEnergyWindowsActor *>(
      GateActorManager::GetActor(fInputActorName));
  fRussianRouletteValue = DictGetInt(user_info, "russian_roulette");
  // init
  fRussianRouletteFactor = 1.0 / fRussianRouletteValue;
}

void GateARFTrainingDatasetActor::StartSimulationAction() {
  fHits = GateHitsCollectionManager::GetInstance()->NewHitsCollection(
      fHitsCollectionName);
  fHits->SetFilename(fOutputFilename);
  // create the attributes
  auto *att_e = new GateTHitAttribute<double>("E");
  auto *att_t = new GateTHitAttribute<double>("Theta");
  auto *att_p = new GateTHitAttribute<double>("Phi");
  auto *att_w = new GateTHitAttribute<double>("window");
  // create the hits collection
  fHits->StartInitialization();
  fHits->InitializeHitAttribute(att_e);
  fHits->InitializeHitAttribute(att_t);
  fHits->InitializeHitAttribute(att_p);
  fHits->InitializeHitAttribute(att_w);
  fHits->FinishInitialization();
  fHits->InitializeRootTupleForMaster();
  // prepare the pointers to the attributes
  fAtt_E = fHits->GetHitAttribute("E");
  fAtt_Theta = fHits->GetHitAttribute("Theta");
  fAtt_Phi = fHits->GetHitAttribute("Phi");
  fAtt_W = fHits->GetHitAttribute("window");
}

void GateARFTrainingDatasetActor::BeginOfEventAction(const G4Event *event) {
  GateHitsCollectionActor::BeginOfEventAction(event);
  // some events will never reach the detector,
  // we used fE == -1 to detect and ignore them
  fThreadLocalData.Get().fE = -1;
}

void GateARFTrainingDatasetActor::SteppingAction(G4Step *step) {
  auto &l = fThreadLocalData.Get();
  /*
   A gamma reach the detector, we store the energy and direction.
   It will be used at the end of the event, once the digitization process end.
   */
  // Get all values, will be filled at end of events.
  auto *pre = step->GetPreStepPoint();
  l.fE = pre->GetKineticEnergy();
  const auto *theTouchable = step->GetPreStepPoint()->GetTouchable();
  auto dir = pre->GetMomentumDirection();
  dir = theTouchable->GetHistory()->GetTopTransform().TransformAxis(dir);
  dir = dir.unit();
  l.fTheta = acos(dir.y()) / CLHEP::degree;
  l.fPhi = acos(dir.x()) / CLHEP::degree;
}

void GateARFTrainingDatasetActor::EndOfEventAction(const G4Event * /*event*/) {
  auto &l = fThreadLocalData.Get();
  // If the event did not reach the detector (in the stepping action), we ignore
  // it.
  if (l.fE == -1)
    return;
  /*
   Now the digitization process is terminated, we can retrieve the associated
   Energy Window id. We retrieve the window id, id=-1 means "outside" WARNING:
   in previous gate versions, outside id was equal to zero, so we stay
   compatible and offset everything by one.
  */
  int w = fEnergyWindowsActor->GetLastEnergyWindowId() + 1;
  // If this is outside, we apply the russian roulette
  if (w == 0) {
    auto x = G4UniformRand();
    if (x > fRussianRouletteFactor)
      return;
  }
  // Fill E, theta, phi and w
  fAtt_E->FillDValue(l.fE);
  fAtt_Theta->FillDValue(l.fTheta);
  fAtt_Phi->FillDValue(l.fPhi);
  fAtt_W->FillDValue(w);
}

void GateARFTrainingDatasetActor::EndSimulationAction() {
  GateHitsCollectionActor::EndSimulationAction();
}
