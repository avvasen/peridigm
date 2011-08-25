//@HEADER
// ************************************************************************
//
//                             Peridigm
//                 Copyright (2011) Sandia Corporation
//
// Under the terms of Contract DE-AC04-94AL85000 with Sandia Corporation,
// the U.S. Government retains certain rights in this software.
//
// Redistribution and use in source and binary forms, with or without
// modification, are permitted provided that the following conditions are
// met:
//
// 1. Redistributions of source code must retain the above copyright
// notice, this list of conditions and the following disclaimer.
//
// 2. Redistributions in binary form must reproduce the above copyright
// notice, this list of conditions and the following disclaimer in the
// documentation and/or other materials provided with the distribution.
//
// 3. Neither the name of the Corporation nor the names of the
// contributors may be used to endorse or promote products derived from
// this software without specific prior written permission.
//
// THIS SOFTWARE IS PROVIDED BY SANDIA CORPORATION "AS IS" AND ANY
// EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
// IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
// PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL SANDIA CORPORATION OR THE
// CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
// EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
// PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
// PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
// LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
// NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
// SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
//
// Questions?
// David J. Littlewood   djlittl@sandia.gov
// John A. Mitchell      jamitch@sandia.gov
// Michael L. Parks      mlparks@sandia.gov
// Stewart A. Silling    sasilli@sandia.gov
//
// ************************************************************************
//@HEADER
#ifndef PHAL_WORKSET_HPP
#define PHAL_WORKSET_HPP

#include <Epetra_Vector.h>
#include <Epetra_Import.h>
#include <vector>
#include <map>
#include "Peridigm_Block.hpp"
#include "Peridigm_DataManager.hpp"
#include "Peridigm_NeighborhoodData.hpp"
#include "Peridigm_Material.hpp"
#include "Peridigm_ContactModel.hpp"

//#define MULTIPLE_BLOCKS

namespace PHAL {

struct Workset {
  
  Workset() {}

  Teuchos::RCP<const double> timeStep;
  Teuchos::RCP<PeridigmNS::SerialMatrix> jacobian;
#ifndef MULTIPLE_BLOCKS
  Teuchos::RCP<PeridigmNS::DataManager> dataManager;
  Teuchos::RCP< std::vector<Teuchos::RCP<const PeridigmNS::Material> > > materialModels;
  Teuchos::RCP<const PeridigmNS::NeighborhoodData> neighborhoodData;
  Teuchos::RCP< std::vector<Teuchos::RCP<const PeridigmNS::ContactModel> > > contactModels;
  Teuchos::RCP<const PeridigmNS::NeighborhoodData> contactNeighborhoodData;
#else
  Teuchos::RCP< std::vector<PeridigmNS::Block> > blocks;
#endif

  // MPI ID (debugging)
  int myPID;
};

}

#endif
